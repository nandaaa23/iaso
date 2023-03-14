import React, { useMemo } from 'react';
import { useSafeIntl } from 'bluesquare-components';
import { Box } from '@material-ui/core';
import MESSAGES from '../messages';
import { formatLabel } from '../../../instances/utils';
import { convertValueIfDate } from '../../../../components/Cells/DateTimeCell';
import { Column } from '../../../../types/table';
import { DuplicateEntityForTable } from '../types';
import { useEntityCell } from './useEntityCell';

type UseDupliactionDetailsColumnsArgs = {
    state: DuplicateEntityForTable[];
    setState: (
        // eslint-disable-next-line no-unused-vars
        index: number,
        // eslint-disable-next-line no-unused-vars
        value: DuplicateEntityForTable,
    ) => void;
    setQuery: React.Dispatch<any>;
};

export const useDuplicationDetailsColumns = ({
    state,
    setState,
    setQuery,
}: UseDupliactionDetailsColumnsArgs): Column[] => {
    const { formatMessage } = useSafeIntl();

    return useMemo(() => {
        return [
            {
                Header: formatMessage(MESSAGES.field),
                accessor: 'field',
                resizable: false,
                sortable: true,
                Cell: settings => {
                    return (
                        <span>{formatLabel(settings.row.original.field)}</span>
                    );
                },
            },
            {
                Header: formatMessage(MESSAGES.entityA),
                accessor: 'entity1',
                resizable: false,
                sortable: false,
                Cell: settings => {
                    const { field, entity1, entity2 } = settings.row.original;
                    const onClick = useEntityCell({
                        field,
                        entity1,
                        entity2,
                        key: 'entity1',
                        setQuery,
                        state,
                        setState,
                    });
                    return (
                        <Box onClick={onClick}>
                            {convertValueIfDate(
                                settings.row.original.entity1.value,
                            )}
                        </Box>
                    );
                },
            },
            {
                Header: formatMessage(MESSAGES.entityB),
                accessor: 'entity2',
                resizable: false,
                sortable: false,
                Cell: settings => {
                    const { field, entity1, entity2 } = settings.row.original;
                    const onClick = useEntityCell({
                        field,
                        entity1,
                        entity2,
                        key: 'entity2',
                        setQuery,
                        state,
                        setState,
                    });

                    return (
                        // eslint-disable-next-line jsx-a11y/no-static-element-interactions
                        <div onClick={onClick}>
                            {convertValueIfDate(
                                settings.row.original.entity2.value,
                            )}
                        </div>
                    );
                },
            },
            {
                Header: formatMessage(MESSAGES.finalValue),
                accessor: 'final',
                resizable: false,
                sortable: false,
                Cell: settings => {
                    const { final } = settings.row.original;
                    return <div>{convertValueIfDate(final.value)}</div>;
                },
            },
        ];
    }, [formatMessage, setQuery, setState, state]);
};
