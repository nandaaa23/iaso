import React, { ReactElement } from 'react';
import { IconButton as IconButtonComponent } from 'bluesquare-components';
import EntityTypesDialog from './components/EntityTypesDialog';
import DeleteDialog from '../../../components/dialogs/DeleteDialogComponent';
import { DateTimeCell } from '../../../components/Cells/DateTimeCell';

import MESSAGES from './messages';

import { baseUrls } from '../../../constants/urls';

import { EntityType } from './types/entityType';

export const baseUrl = baseUrls.entityTypes;

type Message = {
    id: string;
    defaultMessage: string;
};

type Column = {
    Header: string;
    id?: string;
    accessor: string;
    sortable?: boolean;
    resizable?: boolean;
    // eslint-disable-next-line no-unused-vars
    Cell?: (s: any) => ReactElement;
};

type Props = {
    // eslint-disable-next-line no-unused-vars
    formatMessage: (msg: Message) => string;
    // eslint-disable-next-line no-unused-vars
    deleteEntitiyType: (e: EntityType) => void;
    // eslint-disable-next-line no-unused-vars
    saveEntityType: (e: EntityType) => void;
};

export const columns = ({
    formatMessage,
    deleteEntitiyType,
    saveEntityType,
}: Props): Array<Column> => [
    {
        Header: formatMessage(MESSAGES.name),
        id: 'name',
        accessor: 'name',
    },
    {
        Header: formatMessage(MESSAGES.created_at),
        accessor: 'created_at',
        Cell: DateTimeCell,
    },
    {
        Header: formatMessage(MESSAGES.updated_at),
        accessor: 'updated_at',
        Cell: DateTimeCell,
    },
    {
        Header: formatMessage(MESSAGES.entitiesCount),
        accessor: 'entities_count',
        sortable: false,
    },
    {
        Header: formatMessage(MESSAGES.actions),
        accessor: 'actions',
        resizable: false,
        sortable: false,
        Cell: (settings): ReactElement => (
            // TODO: limit to user permissions
            <section>
                {settings.row.original?.defining_form && (
                    <IconButtonComponent
                        url={`/${baseUrls.formDetail}/formId/${settings.row.original.defining_form}`}
                        icon="remove-red-eye"
                        tooltipMessage={MESSAGES.viewForm}
                    />
                )}
                <EntityTypesDialog
                    renderTrigger={({ openDialog }) => (
                        <IconButtonComponent
                            onClick={openDialog}
                            icon="edit"
                            tooltipMessage={MESSAGES.edit}
                        />
                    )}
                    initialData={settings.row.original}
                    titleMessage={MESSAGES.updateMessage}
                    saveEntityType={saveEntityType}
                />
                {settings.row.original.entities_count === 0 && (
                    <DeleteDialog
                        disabled={settings.row.original.instances_count > 0}
                        titleMessage={MESSAGES.deleteTitle}
                        message={MESSAGES.deleteText}
                        onConfirm={() =>
                            deleteEntitiyType(settings.row.original)
                        }
                    />
                )}
            </section>
        ),
    },
];
