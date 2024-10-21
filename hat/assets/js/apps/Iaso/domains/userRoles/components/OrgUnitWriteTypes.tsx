import { Box } from '@mui/material';
import { useSafeIntl } from 'bluesquare-components';
import React, { FunctionComponent } from 'react';
import InputComponent from '../../../components/forms/InputComponent';
import { InputWithInfos } from '../../../components/InputWithInfos';
import { commaSeparatedIdsToArray } from '../../../utils/forms';
import { useGetOrgUnitTypesDropdownOptions } from '../../orgUnits/orgUnitTypes/hooks/useGetOrgUnitTypesDropdownOptions';
import MESSAGES from '../messages';
import { UserRole } from '../types/userRoles';

type Props = {
    userRole: UserRole;
    handleChange: (ouTypesIds: number[]) => void;
};

export const OrgUnitWriteTypes: FunctionComponent<Props> = ({
    userRole,
    handleChange,
}) => {
    const { formatMessage } = useSafeIntl();
    const { data: orgUnitTypes, isLoading: isLoadingOrgUitTypes } =
        useGetOrgUnitTypesDropdownOptions(undefined, true);
    return (
        <Box>
            <InputWithInfos
                infos={formatMessage(MESSAGES.orgUnitWriteTypesInfos)}
            >
                <InputComponent
                    multi
                    clearable
                    keyValue="allow_creating_sub_unit_type_ids"
                    onChange={(_, value) =>
                        handleChange(commaSeparatedIdsToArray(value))
                    }
                    loading={isLoadingOrgUitTypes}
                    value={userRole.editable_org_unit_type_ids ?? []}
                    type="select"
                    options={orgUnitTypes}
                    label={MESSAGES.orgUnitWriteTypes}
                    helperText={formatMessage(MESSAGES.selectAllHelperText)}
                />
            </InputWithInfos>
        </Box>
    );
};
