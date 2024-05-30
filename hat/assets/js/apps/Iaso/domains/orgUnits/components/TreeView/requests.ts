import { UseQueryResult } from 'react-query';
import { errorSnackBar } from '../../../../constants/snackBars';
import { getRequest } from '../../../../libs/Api';
import { useSnackQuery } from '../../../../libs/apiHooks';
import { enqueueSnackbar } from '../../../../redux/snackBarsReducer';
import { dispatch } from '../../../../redux/store';
import { OrgUnit, OrgUnitStatus } from '../../types/orgUnit';

const getValidationStatus = (statusSettings: OrgUnitStatus[]): string => {
    return statusSettings
        .map(status => `&validation_status=${status}`)
        .join('');
};

const baseApiUrl = '/api/orgunits/tree/';

export const getChildrenData = async (
    id: string,
    statusSettings: OrgUnitStatus[],
): Promise<OrgUnit[]> => {
    try {
        const response = await getRequest(
            `${baseApiUrl}?parent_id=${id}&ignoreEmptyNames=true${getValidationStatus(
                statusSettings,
            )}`,
        );
        return response.map((orgUnit: any) => ({
            ...orgUnit,
            id: orgUnit.id.toString(),
        }));
    } catch (error: unknown) {
        dispatch(
            enqueueSnackbar(errorSnackBar('getChildrenDataError', null, error)),
        );
        console.error('Error while fetching Treeview item children:', error);
        throw error;
    }
};

const makeUrl = (
    id?: string | number,
    type?: string,
    statusSettings: OrgUnitStatus[] = ['VALID'],
): string => {
    const validationStatusString = getValidationStatus(statusSettings);
    let typePrefix;

    switch (type) {
        case 'version':
            typePrefix = 'version';
            break;
        case 'source':
            typePrefix = 'data_source_id';
            break;
        default:
            break;
    }

    const idParam = id && typePrefix ? `&${typePrefix}=${id}` : '';
    return `${baseApiUrl}?ignoreEmptyNames=true${idParam}${validationStatusString}`;
};

export const getRootData = async (
    id?: string | number,
    type = 'source',
    statusSettings: OrgUnitStatus[] = ['VALID'],
): Promise<OrgUnit[]> => {
    try {
        const response = await getRequest(makeUrl(id, type, statusSettings));
        return response.map((orgUnit: any) => ({
            ...orgUnit,
            id: orgUnit.id.toString(),
        }));
    } catch (error: unknown) {
        dispatch(
            enqueueSnackbar(errorSnackBar('getRootDataError', null, error)),
        );
        console.error('Error while fetching Treeview items:', error);
        throw error;
    }
};

const endpoint = `${baseApiUrl}search`;
const search = (
    input1: string,
    statusSettings: OrgUnitStatus[] = ['VALID'],
    input2?: string | number,
    type?: string,
): string => {
    const validationStatusString = getValidationStatus(statusSettings);
    let typeParam = '';

    if (type === 'version') {
        typeParam = `&version=${input2}`;
    } else if (type === 'source') {
        typeParam = `&data_source_id=${input2}`;
    }

    return `search=${input1}${typeParam}${validationStatusString}`;
};
const sortingAndPaging = (resultsCount: number): string =>
    `order=name&page=1&limit=${resultsCount}&smallSearch=true`;

const makeSearchUrl = ({
    value,
    count,
    source,
    version,
    statusSettings = ['VALID'],
}: {
    value: string;
    count: number;
    source?: string | number;
    version?: string | number;
    statusSettings?: OrgUnitStatus[];
}): string => {
    let searchType = '';
    if (source) {
        searchType = 'source';
    } else if (version) {
        searchType = 'version';
    }
    const searchId = source || version;
    return `${endpoint}?${search(
        value,
        statusSettings,
        searchId,
        searchType,
    )}&${sortingAndPaging(count)}`;
};

export const searchOrgUnits = async ({
    value,
    count,
    source,
    version,
    statusSettings = ['VALID'],
}: {
    value: string;
    count: number;
    source?: string | number;
    version?: string | number;
    statusSettings?: OrgUnitStatus[];
}): Promise<OrgUnit[]> => {
    try {
        const url = makeSearchUrl({
            value,
            count,
            source,
            version,
            statusSettings,
        });
        const result = await getRequest(url);
        return result.results;
    } catch (error: unknown) {
        dispatch(
            enqueueSnackbar(errorSnackBar('searchOrgUnitsError', null, error)),
        );
        console.error('Error while searching org units:', error);
        throw error;
    }
};

export const useGetOrgUnit = (
    OrgUnitId: string | undefined,
): UseQueryResult<OrgUnit, Error> =>
    useSnackQuery(
        ['orgunits', OrgUnitId],
        () => getRequest(`/api/orgunits/${OrgUnitId}/`),
        undefined,
        {
            enabled: !!OrgUnitId,
        },
    );

const getOrgUnits = async (
    orgUnitsIds: string[] | string,
    statusSettings = 'all',
): Promise<OrgUnit[]> => {
    const idsString = Array.isArray(orgUnitsIds)
        ? orgUnitsIds.join(',')
        : orgUnitsIds;
    const searchParam = `[{"validation_status":"${statusSettings}","search": "ids:${idsString}" }]`;
    return getRequest(`/api/orgunits/?limit=10&searches=${searchParam}`);
};

export const useGetMultipleOrgUnits = (
    orgUnitsIds: string[] | string,
    statusSettings = 'all',
): UseQueryResult<OrgUnit[], Error> => {
    return useSnackQuery({
        queryKey: ['orgunits', orgUnitsIds, statusSettings],
        queryFn: () => getOrgUnits(orgUnitsIds, statusSettings),
        options: {
            enabled: Boolean(orgUnitsIds?.length),
            select: (data: any) => (data ? data.orgunits : {}),
        },
    });
};
