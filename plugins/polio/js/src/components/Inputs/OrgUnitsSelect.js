import { Select } from './Select';
import { useGetOrgUnits } from '../../hooks/useGetOrgUnits';
import { useState, useEffect } from 'react';
import { useGetAuthenticatedUser } from '../../hooks/useGetAuthenticatedUser';

export const OrgUnitsSelect = props => {
    const { level, source, addLevel } = props;
    const { data = {} } = useGetOrgUnits(level, source);
    const { orgUnits = [] } = data;

    return (
        <Select
            {...props}
            options={orgUnits.map(orgUnit => ({
                value: orgUnit.id,
                label: orgUnit.name,
            }))}
            onChange={event => {
                addLevel({
                    parent_id: level,
                    org_unit_id: event.target.value,
                });
            }}
        />
    );
};

export const OrgUnitsLevels = ({ field = {}, form, ...props }) => {
    const { data = {}, isLoading } = useGetAuthenticatedUser();
    const [levels, setLevel] = useState([0]);
    const { name } = field;
    const { setFieldValue } = form;

    useEffect(() => {
        setFieldValue(name, levels[levels.length - 1]);
    }, [levels, name, setFieldValue]);

    const addLevel = ({ parent_id = 0, org_unit_id }) => {
        setLevel(oldLevels => {
            const index = oldLevels.indexOf(parent_id);
            return [...oldLevels.slice(0, index + 1), org_unit_id];
        });
    };

    if (isLoading) {
        return null;
    }

    const source = data?.account?.default_version?.data_source?.id;

    return levels.map((level, index) => {
        return (
            <OrgUnitsSelect
                key={level}
                source={source}
                label={`Level ${index + 1}`}
                level={level}
                addLevel={addLevel}
            />
        );
    });
};

export default OrgUnitsSelect;
