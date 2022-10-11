import React, { FunctionComponent } from 'react';
// @ts-ignore
import { makeStyles, Box } from '@material-ui/core';
// @ts-ignore
import { commonStyles, useSafeIntl } from 'bluesquare-components';
import { useDispatch } from 'react-redux';

import TopBar from '../../components/nav/TopBarComponent';
import { TableWithDeepLink } from '../../components/tables/TableWithDeepLink';
import { StorageParams } from './types/storages';
import { Filters } from './components/Filters';
import { useGetStorages } from './hooks/requests/useGetStorages';
import { redirectTo } from '../../routing/actions';

import { baseUrls } from '../../constants/urls';
import MESSAGES from './messages';
import { Columns } from './config';

const useStyles = makeStyles(theme => ({
    ...commonStyles(theme),
}));

type Props = {
    params: StorageParams;
};

const baseUrl = baseUrls.storages;
export const Storages: FunctionComponent<Props> = ({ params }) => {
    const dispatch = useDispatch();
    const classes: Record<string, string> = useStyles();
    const { formatMessage } = useSafeIntl();
    const { data, isFetching } = useGetStorages(params);
    return (
        <>
            <TopBar
                title={formatMessage(MESSAGES.title)}
                displayBackButton={false}
            />
            <Box className={classes.containerFullHeightNoTabPadded}>
                <Filters params={params} />
                <TableWithDeepLink
                    baseUrl={baseUrl}
                    data={data?.results ?? []}
                    pages={data?.pages ?? 1}
                    defaultSorted={[{ id: 'name', desc: false }]}
                    columns={Columns(formatMessage)}
                    count={data?.count ?? 0}
                    params={params}
                    onTableParamsChange={p => dispatch(redirectTo(baseUrl, p))}
                    extraProps={{ loading: isFetching }}
                />
            </Box>
        </>
    );
};
