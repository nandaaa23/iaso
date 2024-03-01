/* eslint-disable camelcase */
import React, { FunctionComponent } from 'react';
import { TableBody } from '@mui/material';
import { NewOrgUnitField } from '../../hooks/useNewFields';
import { ReviewOrgUnitChangesDetailsTableRow } from './ReviewOrgUnitChangesDetailsTableRow';
import { OrgUnitChangeRequestDetails } from '../../types';
import { HighlightFields } from '../../Dialogs/HighlightFieldsChanges';
import { sortBy } from 'lodash';

type Props = {
    newFields: NewOrgUnitField[];
    // eslint-disable-next-line no-unused-vars
    setSelected: (key: string) => void;
    isFetchingChangeRequest: boolean;
    changeRequest?: OrgUnitChangeRequestDetails;
    isNew: boolean;
};

export const ReviewOrgUnitChangesDetailsTableBody: FunctionComponent<Props> = ({
    newFields,
    setSelected,
    isFetchingChangeRequest,
    changeRequest,
    isNew,
}) => {
    return (
        <TableBody>
            {newFields.map(field => {
                if (field.key === 'groups') {
                    const changedFieldWithNewValues =
                        changeRequest && changeRequest[`new_${field.key}`];
                    const changedFieldWithOldValues =
                        changeRequest && changeRequest[`old_${field.key}`];

                    return (
                        <HighlightFields
                            label={field.label}
                            field={field}
                            newGroups={sortBy(changedFieldWithNewValues, 'id')}
                            oldGroups={sortBy(changedFieldWithOldValues, 'id')}
                            status={changeRequest?.status || ""}
                            isNew={isNew}
                            setSelected={setSelected}
                        />
                    );
                } else {
                    return (
                        <ReviewOrgUnitChangesDetailsTableRow
                            key={field.key}
                            field={field}
                            setSelected={setSelected}
                            isNew={isNew}
                            changeRequest={changeRequest}
                            isFetchingChangeRequest={isFetchingChangeRequest}
                        />
                    );
                }
            })}
        </TableBody>
    );
};
