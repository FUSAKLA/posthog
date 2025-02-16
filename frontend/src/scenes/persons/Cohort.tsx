import React from 'react'
import { CohortGroup } from './CohortGroup'
import { cohortLogic } from './cohortLogic'
import { Button, Card, Col, Divider, Input, Row } from 'antd'
import { UploadOutlined, AimOutlined, ArrowLeftOutlined, InboxOutlined } from '@ant-design/icons'
import { useValues, useActions } from 'kea'
import { CohortType } from '~/types'
import { Persons } from './Persons'
import { cohortLogicType } from 'types/scenes/persons/cohortLogicType'
import Dragger from 'antd/lib/upload/Dragger'

const isSubmitDisabled = (cohort: CohortType): boolean => {
    if (cohort && cohort.csv) {
        return false
    }
    if (cohort && cohort.groups) {
        return !cohort.groups.some((group) => Object.keys(group).length)
    }
    return true
}

function StaticCohort({ logic }: { logic: cohortLogicType }): JSX.Element {
    const { setCohort } = useActions(logic)
    const { cohort } = useValues(logic)
    const props = {
        name: 'file',
        multiple: false,
        fileList: cohort.csv ? [cohort.csv] : [],
        beforeUpload(file: File) {
            setCohort({ ...cohort, csv: file })

            return false
        },
        accept: '.csv',
    }
    return (
        <>
            {cohort.id === 'new' && (
                <>
                    <Button size="small" type="link" onClick={() => setCohort({ ...cohort, is_static: undefined })}>
                        <ArrowLeftOutlined /> Create dynamic cohort instead
                    </Button>
                    <br />
                    <br />
                </>
            )}
            <Dragger {...props}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                </p>
                <p className="ant-upload-text">Click or drag CSV to this area to upload</p>
                <p className="ant-upload-hint">
                    Make sure the file has a single column with either the user's distinct_id or email.
                </p>
            </Dragger>
            {cohort.id !== 'new' && (
                <p style={{ marginTop: '1rem' }}>
                    This is a static cohort with <strong>{cohort.count}</strong> user{cohort.count !== 1 && 's'}. If you
                    upload another .csv file, those users will be added to this cohort.
                </p>
            )}
        </>
    )
}

function DynamicCohort({ logic }: { logic: cohortLogicType }): JSX.Element {
    const { setCohort } = useActions(logic)
    const { cohort } = useValues(logic)
    return (
        <>
            {cohort.id === 'new' && (
                <>
                    <Button size="small" type="link" onClick={() => setCohort({ ...cohort, is_static: undefined })}>
                        <ArrowLeftOutlined /> Create cohort by CSV instead
                    </Button>
                    <br />
                    <br />
                </>
            )}
            {cohort.groups.map((group, index) => (
                <React.Fragment key={index}>
                    <CohortGroup
                        group={group}
                        allowRemove={cohort.groups.length > 1}
                        index={index}
                        onRemove={() => {
                            cohort.groups.splice(index, 1)
                            setCohort({ ...cohort })
                        }}
                        onChange={(group: Record<string, any>) => {
                            cohort.groups[index] = group
                            setCohort({ ...cohort })
                        }}
                    />
                    {index < cohort.groups.length - 1 && (
                        <div key={index} className="secondary" style={{ textAlign: 'center', margin: 8 }}>
                            {' '}
                            OR{' '}
                        </div>
                    )}
                </React.Fragment>
            ))}
        </>
    )
}

function CohortChoice({ setCohort, cohort }: { setCohort: CallableFunction; cohort: CohortType }): JSX.Element {
    return (
        <Row gutter={24}>
            <Col sm={12}>
                <Card
                    title="Upload CSV"
                    size="small"
                    className="clickable-card"
                    data-attr="cohort-choice-upload-csv"
                    onClick={() => setCohort({ ...cohort, is_static: true })}
                >
                    <div style={{ textAlign: 'center', fontSize: 40 }}>
                        <UploadOutlined />
                    </div>
                </Card>
            </Col>
            <Col sm={12}>
                <Card
                    title="Create cohort by definition"
                    size="small"
                    className="clickable-card"
                    data-attr="cohort-choice-definition"
                    onClick={() => setCohort({ ...cohort, is_static: false })}
                >
                    <div style={{ textAlign: 'center', fontSize: 40 }}>
                        <AimOutlined />
                    </div>
                </Card>
            </Col>
        </Row>
    )
}

export function Cohort(props: { onChange: CallableFunction; cohort: CohortType }): JSX.Element {
    const logic = cohortLogic(props)
    const { setCohort, saveCohort } = useActions(logic)
    const { cohort, lastSavedAt } = useValues(logic)

    return (
        <div style={{ maxWidth: 750 }} className="mb">
            <form
                onSubmit={(e): void => {
                    e.preventDefault()
                    saveCohort(cohort)
                }}
            >
                <div className="mb">
                    <Input
                        required
                        autoFocus
                        placeholder="Cohort name..."
                        value={cohort.name}
                        data-attr="cohort-name"
                        onChange={(e) => setCohort({ ...cohort, name: e.target.value })}
                    />
                </div>
                {cohort.id === 'new' && cohort.is_static === undefined && (
                    <CohortChoice cohort={cohort} setCohort={setCohort} />
                )}
                {cohort.is_static && <StaticCohort logic={logic} />}
                {(cohort.is_static === false || (cohort.is_static === null && cohort.id !== 'new')) && (
                    <DynamicCohort logic={logic} />
                )}

                <div className="mt">
                    <Button
                        type="primary"
                        htmlType="submit"
                        disabled={isSubmitDisabled(cohort)}
                        data-attr="save-cohort"
                        style={{ marginTop: '1rem' }}
                    >
                        Save cohort
                    </Button>
                    {!cohort.is_static && (
                        <Button
                            style={{ marginTop: '1rem', marginLeft: 12 }}
                            onClick={() => setCohort({ ...cohort, groups: [...cohort.groups, {}] })}
                        >
                            New group
                        </Button>
                    )}
                </div>
            </form>
            <Divider />
            {cohort.id !== 'new' && <Persons cohort={cohort} key={lastSavedAt} />}
        </div>
    )
}
