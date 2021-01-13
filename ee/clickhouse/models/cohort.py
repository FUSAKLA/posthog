import uuid
from typing import Any, Dict, List, Optional, Tuple

from ee.clickhouse.client import sync_execute
from ee.clickhouse.models.action import format_action_filter
from ee.clickhouse.sql.cohort import CALCULATE_COHORT_PEOPLE_SQL
from ee.clickhouse.sql.person import (
    GET_LATEST_PERSON_ID_SQL,
    GET_PERSON_IDS_BY_FILTER,
    INSERT_PERSON_STATIC_COHORT,
    PERSON_STATIC_COHORT_TABLE,
)
from ee.idl.gen import person_static_cohort_pb2
from ee.kafka_client.client import ClickhouseProducer
from ee.kafka_client.topics import KAFKA_PERSON_STATIC_COHORT
from posthog.models import Action, Cohort, Filter, Team


def format_person_query(cohort: Cohort) -> Tuple[str, Dict[str, Any]]:
    filters = []
    params: Dict[str, Any] = {}

    if cohort.is_static:
        return (
            "person_id IN (SELECT person_id FROM {} WHERE cohort_id = {} AND team_id = {})".format(
                PERSON_STATIC_COHORT_TABLE, cohort.pk, cohort.team_id
            ),
            {},
        )

    for group_idx, group in enumerate(cohort.groups):
        if group.get("action_id"):
            action = Action.objects.get(pk=group["action_id"], team_id=cohort.team.pk)
            action_filter_query, action_params = format_action_filter(action, index=group_idx)
            extract_person = "SELECT distinct_id FROM events WHERE team_id = %(team_id)s AND {query}".format(
                query=action_filter_query
            )
            params = {**params, **action_params}
            filters.append("distinct_id IN (" + extract_person + ")")

        elif group.get("properties"):
            from ee.clickhouse.models.property import prop_filter_json_extract

            filter = Filter(data=group)
            query = ""
            for idx, prop in enumerate(filter.properties):
                filter_query, filter_params = prop_filter_json_extract(
                    prop=prop, idx=idx, prepend="{}_{}_{}_person".format(cohort.pk, group_idx, idx)
                )
                params = {**params, **filter_params}
                query += " {}".format(filter_query)
            filters.append("person_id IN {}".format(GET_LATEST_PERSON_ID_SQL.format(query=query)))

    joined_filter = " OR ".join(filters)
    return joined_filter, params


def format_filter_query(cohort: Cohort) -> Tuple[str, Dict[str, Any]]:
    person_query, params = format_person_query(cohort)
    person_id_query = CALCULATE_COHORT_PEOPLE_SQL.format(query=person_query)
    return person_id_query, params


def get_person_ids_by_cohort_id(team: Team, cohort_id: int):
    from ee.clickhouse.models.property import parse_prop_clauses

    filters = Filter(data={"properties": [{"key": "id", "value": cohort_id, "type": "cohort"}],})
    filter_query, filter_params = parse_prop_clauses(filters.properties, team.pk, table_name="pid")

    results = sync_execute(GET_PERSON_IDS_BY_FILTER.format(distinct_query=filter_query, query=""), filter_params)

    return [str(row[0]) for row in results]


def insert_static_cohort(person_uuids: List[Optional[uuid.UUID]], cohort_id: int, team: Team):
    for person_uuid in person_uuids:
        pb_event = person_static_cohort_pb2.PersonStaticCohort()
        pb_event.id = str(uuid.uuid4())
        pb_event.person_id = str(person_uuid)
        pb_event.cohort_id = cohort_id
        pb_event.team_id = team.pk

        p = ClickhouseProducer()
        p.produce_proto(sql=INSERT_PERSON_STATIC_COHORT, topic=KAFKA_PERSON_STATIC_COHORT, data=pb_event)
