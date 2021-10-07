import React, { useState } from 'react';
import { FormattedMessage } from 'react-intl';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';

import { Grid, Button, Box } from '@material-ui/core';
import FiltersIcon from '@material-ui/icons/FilterList';

import InputComponent from '../../../../../../hat/assets/js/apps/Iaso/components/forms/InputComponent';
import DatesRange from '../../../../../../hat/assets/js/apps/Iaso/components/filters/DatesRange';
import { redirectTo } from '../../../../../../hat/assets/js/apps/Iaso/routing/actions';

import MESSAGES from '../../constants/messages';
import { useGetCountries } from '../../hooks/useGetCountries';

const Filters = ({ params, baseUrl }) => {
    const [filtersUpdated, setFiltersUpdated] = useState(false);
    const [countries, setCountries] = useState(params.countries);
    const [obrName, setObrName] = useState(params.obrName);
    const [obrFrom, setObrFrom] = useState(params.obrFrom);
    const [obrTo, setObrTo] = useState(params.obrTo);
    const dispatch = useDispatch();
    const handleSearch = () => {
        if (filtersUpdated) {
            setFiltersUpdated(false);
            const newParams = {
                ...params,
                countries,
                obrName,
                obrFrom,
                obrTo,
            };
            dispatch(redirectTo(baseUrl, newParams));
        }
    };
    const { data, isFetching: isFetchingCountries } = useGetCountries();
    const countriesList = (data && data.orgUnits) || [];
    return (
        <>
            <Grid container spacing={4}>
                <Grid item xs={3}>
                    <InputComponent
                        loading={isFetchingCountries}
                        keyValue="countries"
                        multi
                        clearable
                        onChange={(key, value) => {
                            setFiltersUpdated(true);
                            setCountries(value);
                        }}
                        value={countries}
                        type="select"
                        options={countriesList.map(c => ({
                            label: c.name,
                            value: c.id,
                        }))}
                        label={MESSAGES.country}
                    />
                </Grid>
                <Grid item xs={3}>
                    <InputComponent
                        keyValue="orbName"
                        onChange={(key, value) => {
                            setFiltersUpdated(true);
                            setObrName(value);
                        }}
                        value={obrName}
                        type="search"
                        label={MESSAGES.name}
                        onEnterPressed={handleSearch}
                    />
                </Grid>
                <Grid item xs={6}>
                    <DatesRange
                        onChangeDate={(key, value) => {
                            if (key === 'dateFrom') {
                                setObrFrom(value);
                            }
                            if (key === 'dateTo') {
                                setObrTo(value);
                            }
                            setFiltersUpdated(true);
                        }}
                        labelFrom={MESSAGES.R1StartFrom}
                        labelTo={MESSAGES.R1StartTo}
                        dateFrom={obrFrom}
                        dateTo={obrTo}
                    />
                </Grid>
            </Grid>
            <Grid
                container
                spacing={4}
                justifyContent="flex-end"
                alignItems="center"
            >
                <Grid
                    item
                    xs={2}
                    container
                    justifyContent="flex-end"
                    alignItems="center"
                >
                    <Button
                        disabled={!filtersUpdated}
                        variant="contained"
                        color="primary"
                        onClick={() => handleSearch()}
                    >
                        <Box mr={1} top={3} position="relative">
                            <FiltersIcon />
                        </Box>
                        <FormattedMessage {...MESSAGES.filter} />
                    </Button>
                </Grid>
            </Grid>
        </>
    );
};

Filters.defaultProps = {
    baseUrl: '',
};

Filters.propTypes = {
    params: PropTypes.object.isRequired,
    baseUrl: PropTypes.string,
};

export { Filters };
