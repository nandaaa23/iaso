import { paginationPathParams } from '../../../../../hat/assets/js/apps/Iaso/routing/common';
import {
    RouteConfig,
    extractParams,
    extractParamsConfig,
    extractUrls,
} from '../../../../../hat/assets/js/apps/Iaso/constants/urls';
import {
    DESTRUCTION,
    FORM_A,
    INCIDENT,
    UNUSABLE_VIALS,
    USABLE_VIALS,
} from '../domains/VaccineModule/StockManagement/constants';

export const DASHBOARD_BASE_URL = 'polio/list';
export const CAMPAIGN_HISTORY_URL = 'polio/campaignHistory';
export const CALENDAR_BASE_URL = 'polio/calendar';
export const EMBEDDED_CALENDAR_URL = 'polio/embeddedCalendar';
export const CONFIG_BASE_URL = 'polio/config';
export const CONFIG_COUNTRY_URL = `${CONFIG_BASE_URL}/country`;
export const CONFIG_REASONS_FOR_DELAY_URL = `${CONFIG_BASE_URL}/reasonsfordelay`;
export const LQAS_BASE_URL = 'polio/lqas/lqas';
export const LQAS_AFRO_MAP_URL = 'polio/lqas/lqas-map';
export const IM = 'polio/im';
export const GROUPED_CAMPAIGNS = 'polio/groupedcampaigns';
export const BUDGET = 'polio/budget';
export const BUDGET_DETAILS = 'polio/budget/details';
export const VACCINE_MODULE = 'polio/vaccinemodule';
export const NOPV2_AUTH = `${VACCINE_MODULE}/nopv2authorisation`;
export const NOPV2_AUTH_DETAILS = `${NOPV2_AUTH}/details`;
export const VACCINE_SUPPLY_CHAIN = `${VACCINE_MODULE}/supplychain`;
export const VACCINE_SUPPLY_CHAIN_DETAILS = `${VACCINE_SUPPLY_CHAIN}/details`;
export const STOCK_MANAGEMENT = `${VACCINE_MODULE}/stockmanagement`;
export const STOCK_MANAGEMENT_DETAILS = `${STOCK_MANAGEMENT}/details`;
export const STOCK_VARIATION = `${STOCK_MANAGEMENT}/variation`;
export const NOTIFICATIONS_BASE_URL = 'polio/notifications';

export const campaignParams = [
    'countries',
    'search',
    'roundStartFrom',
    'roundStartTo',
    'showOnlyDeleted',
    'campaignType',
    'campaignCategory',
    'campaignGroups',
    'show_test',
    'filterLaunched',
];

export const polioRouteConfigs: Record<string, RouteConfig> = {
    dashboard: {
        url: DASHBOARD_BASE_URL,
        params: [
            ...paginationPathParams,
            'campaignId',
            ...campaignParams,
            'fieldset',
            'orgUnitGroups',
        ],
    },
    campaignHistory: {
        url: CAMPAIGN_HISTORY_URL,
        params: ['campaignId', 'logId'],
    },
    groupedCampaigns: {
        url: GROUPED_CAMPAIGNS,
        params: [...paginationPathParams, 'campaignId', ...campaignParams],
    },
    calendar: {
        url: CALENDAR_BASE_URL,
        params: [
            'currentDate',
            'order',
            ...campaignParams,
            'orgUnitGroups',
            'periodType',
        ],
    },
    embeddedCalendar: {
        url: EMBEDDED_CALENDAR_URL,
        params: [
            'currentDate',
            'order',
            ...campaignParams,
            'orgUnitGroups',
            'periodType',
        ],
    },
    lqasCountry: {
        url: LQAS_BASE_URL,
        params: ['campaign', 'country', 'rounds', 'leftTab', 'rightTab'],
    },
    lqasAfro: {
        url: LQAS_AFRO_MAP_URL,
        params: [
            'rounds',
            'startDate',
            'endDate',
            'period',
            'displayedShapesLeft',
            'zoomLeft',
            'centerLeft',
            'zoomRight',
            'centerRight',
            'displayedShapesRight',
            'leftTab',
            'rightTab',
        ],
    },
    im: {
        url: IM,
        params: ['imType', 'campaign', 'country', 'rounds'],
    },
    budget: {
        url: BUDGET,
        params: [
            ...paginationPathParams,
            'search',
            'budget_current_state_key__in',
            'roundStartFrom',
            'roundStartTo',
            'country__id__in',
            'orgUnitGroups',
        ],
    },
    budgetDetails: {
        url: BUDGET_DETAILS,
        params: [
            ...paginationPathParams,
            'campaignName',
            'campaignId',
            'country',
            'show_hidden',
            'action',
            'quickTransition',
            'previousStep',
            'transition_key',
        ],
    },
    nopv2Auth: {
        url: NOPV2_AUTH,
        params: [...paginationPathParams, 'auth_status', 'block_country'],
    },
    nopv2AuthDetails: {
        url: NOPV2_AUTH_DETAILS,
        params: [...paginationPathParams, 'country', 'countryName'],
    },
    vaccineSupplyChain: {
        url: VACCINE_SUPPLY_CHAIN,
        params: [
            ...paginationPathParams,
            'search',
            'campaign__country',
            'vaccine_type',
            'rounds__started_at__gte',
            'rounds__started_at__lte',
            'country_blocks',
        ],
    },
    vaccineSupplyChainDetails: {
        url: VACCINE_SUPPLY_CHAIN_DETAILS,
        params: ['id', 'tab'],
    },
    stockManagement: {
        url: STOCK_MANAGEMENT,
        params: [
            ...paginationPathParams,
            'search',
            'country_id',
            'vaccine_type',
            'country_blocks',
        ],
    },
    stockManagementDetails: {
        url: STOCK_MANAGEMENT_DETAILS,
        params: [
            `id`,
            `tab`,
            `${USABLE_VIALS}Order`,
            `${USABLE_VIALS}PageSize`,
            `${USABLE_VIALS}Page`,
            `${UNUSABLE_VIALS}Order`,
            `${UNUSABLE_VIALS}PageSize`,
            `${UNUSABLE_VIALS}Page`,
        ],
    },
    stockVariation: {
        url: STOCK_VARIATION,
        params: [
            `id`,
            `tab`,
            `${FORM_A}Order`,
            `${FORM_A}PageSize`,
            `${FORM_A}Page`,
            `${DESTRUCTION}Order`,
            `${DESTRUCTION}PageSize`,
            `${DESTRUCTION}Page`,
            `${INCIDENT}Order`,
            `${INCIDENT}PageSize`,
            `${INCIDENT}Page`,
        ],
    },
    countryConfig: {
        url: CONFIG_COUNTRY_URL,
        params: [...paginationPathParams],
    },
    reasonsForDelayConfig: {
        url: CONFIG_REASONS_FOR_DELAY_URL,
        params: [...paginationPathParams],
    },
    notification: {
        url: NOTIFICATIONS_BASE_URL,
        params: [
            ...paginationPathParams,
            'vdpv_category',
            'source',
            'country',
            'date_of_onset_after',
            'date_of_onset_before',
        ],
    },
};

export type PolioBaseUrls = {
    dashboard: string;
    campaignHistory: string;
    groupedCampaigns: string;
    calendar: string;
    lqasCountry: string;
    lqasAfro: string;
    im: string;
    budget: string;
    budgetDetails: string;
    nopv2Auth: string;
    nopv2AuthDetails: string;
    vaccineSupplyChain: string;
    vaccineSupplyChainDetails: string;
    stockManagement: string;
    stockManagementDetails: string;
    stockVariation: string;
    countryConfig: string;
    reasonsForDelayConfig: string;
    embeddedCalendar: string;
    notification: string;
};
export const baseUrls = extractUrls(polioRouteConfigs) as PolioBaseUrls;
export const baseParams = extractParams(polioRouteConfigs);
export const paramsConfig = extractParamsConfig(polioRouteConfigs);
