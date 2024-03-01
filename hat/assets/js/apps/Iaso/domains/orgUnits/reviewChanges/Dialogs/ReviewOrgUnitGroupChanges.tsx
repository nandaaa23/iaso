import React, { FunctionComponent } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    TableRow,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { NestedGroup } from '../types';
import { NewOrgUnitField } from '../hooks/useNewFields';

type Props = {
    groups: NestedGroup[];
    newAddedGroups: NestedGroup[];
    status: string | undefined;
    field: NewOrgUnitField;
};

export const ReviewOrgUnitGroupChanges: FunctionComponent<Props> = ({
    groups,
    newAddedGroups,
    status,
    field,
}) => {
    const isCellApproved = (status && status === 'approved' && 'success.light') || '';
    const isSelected = (status && field?.isSelected === true && "success.light") || "";
    
    return (
        <Accordion>
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1-content"
                id="panel1-header"
            >
                View details
            </AccordionSummary>
            <AccordionDetails>
                <Table>
                    <TableBody>
                        {groups.map(group => {
                            const { name } = group;
                            const isNewElement =
                                newAddedGroups?.includes(group);
                            const selected = isSelected;
                            return (
                                <TableRow>
                                    <TableCell
                                        sx={{
                                            color: (selected !== "" && selected) ||
                                                (isNewElement &&
                                                    'error.light') ||
                                                isCellApproved,
                                            borderBottom: 'none',
                                        }}
                                    >
                                        {name}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </AccordionDetails>
        </Accordion>
    );
};
