import { Chip } from '@mui/material';
import { makeStyles } from '@mui/styles';
import { Column, IconButton, useSafeIntl } from 'bluesquare-components';
import React, { useMemo } from 'react';
import { DateTimeCell } from '../../../components/Cells/DateTimeCell';
import { DisplayIfUserHasPerm } from '../../../components/DisplayIfUserHasPerm';
import { baseUrls } from '../../../constants/urls';
import MESSAGES from './messages';

import DeleteDialog from '../../../components/dialogs/DeleteDialogComponent';
import * as Permission from '../../../utils/permissions';

export const baseUrl = baseUrls.groupSets;

const useStyles = makeStyles(theme => ({
    groupChip: {
        margin: '2px',
    },
}));

export const useGroupSetsTableColumns = (deleteGroupSet): Column[] => {
    const classes = useStyles();
    const { formatMessage } = useSafeIntl();
    return useMemo(
        () => [
            {
                Header: 'Id',
                accessor: 'id',
                width: 80,
            },

            {
                Header: 'Name',
                accessor: 'name',
                width: 80,
            },

            {
                Header: 'Groups',
                accessor: 'groups',
                sortable: false,
                width: 200,
                Cell: settings => {
                    settings.row.original.groups.sort((a, b) =>
                        a.name > b.name ? 1 : b.name > a.name ? -1 : 0,
                    );
                    return (
                        <span>
                            {settings.row.original.groups.map(g => (
                                <Chip
                                    className={classes.groupChip}
                                    label={g.name}
                                    color="primary"
                                    key={g.id}
                                />
                            ))}
                        </span>
                    );
                },
            },

            {
                Header: formatMessage(MESSAGES.created_at),
                accessor: 'created_at',
                Cell: DateTimeCell,
                width: 60,
            },

            {
                Header: formatMessage(MESSAGES.updated_at),
                accessor: 'updated_at',
                Cell: DateTimeCell,
                width: 60,
            },
            {
                Header: formatMessage(MESSAGES.actions),
                resizable: false,
                accessor: 'action',
                sortable: false,
                width: 100,
                Cell: settings => (
                    <section>
                        <DisplayIfUserHasPerm
                            permissions={[Permission.ORG_UNIT_GROUPS]}
                        >
                            <IconButton
                                url={`/${baseUrls.groupSetDetail}/groupSetId/${settings.row.original.id}`}
                                icon="edit"
                                tooltipMessage={MESSAGES.edit}
                            />
                            <DeleteDialog
                                keyName="groupSet"
                                titleMessage={MESSAGES.delete}
                                message={MESSAGES.deleteWarning}
                                onConfirm={() =>
                                    deleteGroupSet(settings.row.original)
                                }
                            />
                        </DisplayIfUserHasPerm>
                    </section>
                ),
            },
        ],
        [],
    );
};
