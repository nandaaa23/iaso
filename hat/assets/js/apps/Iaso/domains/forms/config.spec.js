import formsTableColumns, { formVersionsTableColumns } from './config';
import IconButtonComponent from '../../components/buttons/IconButtonComponent';

import formsFixture from './fixtures/forms.json';
import formVersionsfixture from './fixtures/formVersions.json';

const defaultProps = {
    state: {
        currentOrgUnit: undefined,
    },
    setState: () => null,
    deleteForm: () => null,
};

let columns;
let formVersionscolumns;
const fakeForm = formsFixture.forms[0];
const fakeFormVersion = formVersionsfixture.form_versions[0];
let wrapper;
let xlsButton;

describe('Forms config', () => {
    describe('formVersionsTableColumns', () => {
        it('sould return an array of 4 columns', () => {
            formVersionscolumns = formVersionsTableColumns(() => null);
            expect(formVersionscolumns).to.have.lengthOf(4);
        });
        it('should render a component if Cell is defined', () => {
            formVersionscolumns.forEach(c => {
                if (c.Cell) {
                    const cell = c.Cell({
                        original: fakeFormVersion,
                    });
                    expect(cell).to.exist;
                }
            });
        });
        it('should open a tabon click on xls icon', () => {
            const actionColumn =
                formVersionscolumns[formVersionscolumns.length - 1];
            wrapper = shallow(
                actionColumn.Cell({
                    original: fakeFormVersion,
                }),
            );
            xlsButton = wrapper.find(IconButtonComponent);

            expect(xlsButton).to.have.lengthOf(1);
            const openStub = sinon.stub(window, 'open');
            xlsButton.props().onClick();
            expect(openStub).to.have.been.called;
            sinon.restore();
        });
    });
    describe('formsTableColumns', () => {
        it('sould return an array of 9 columns', () => {
            columns = formsTableColumns(() => null, defaultProps);
            expect(columns).to.have.lengthOf(9);
        });
        it('should render a component if Cell is defined', () => {
            columns.forEach(c => {
                if (c.Cell) {
                    const cell = c.Cell({
                        original: fakeForm,
                    });
                    expect(cell).to.exist;
                }
            });
        });
        it('should render a component if value not present and Cell is defined', () => {
            const tempForm = { ...fakeForm };
            delete tempForm.instance_updated_at;
            columns.forEach(c => {
                if (c.Cell) {
                    const cell = c.Cell({
                        original: tempForm,
                    });
                    expect(cell).to.exist;
                }
            });
        });
        describe('action colmumn', () => {
            it('should only display eye icon button if instances_count = 0,showEditAction = false, showMappingAction = false', () => {
                const tempForm = { ...fakeForm };
                columns = formsTableColumns(
                    () => null,
                    defaultProps,
                    false,
                    false,
                );
                tempForm.instances_count = 0;
                const actionColumn = columns[columns.length - 1];
                wrapper = shallow(
                    actionColumn.Cell({
                        original: tempForm,
                    }),
                );

                const redEyeIcon = wrapper.find('[icon="remove-red-eye"]');
                expect(redEyeIcon).to.have.lengthOf(1);
                const editIcon = wrapper.find('[icon="edit"]');
                expect(editIcon).to.have.lengthOf(0);
                const dhisIcon = wrapper.find('[icon="dhis"]');
                expect(dhisIcon).to.have.lengthOf(0);
                expect(wrapper.find(IconButtonComponent)).to.have.lengthOf(1);
            });
            it('should change url if currentOrg unit is defined and display red eye icon', () => {
                const tempForm = { ...fakeForm };
                tempForm.instances_count = 5;
                columns = formsTableColumns(
                    () => null,
                    { ...defaultProps, state: { currentOrgUnit: { id: 1 } } },
                    false,
                    false,
                );
                const actionColumn = columns[columns.length - 1];
                wrapper = shallow(
                    actionColumn.Cell({
                        original: tempForm,
                    }),
                );
                const redEyeIcon = wrapper.find('[icon="remove-red-eye"]');
                expect(redEyeIcon.prop('url')).to.equal(
                    'instances/formId/14/levels/1',
                );
                expect(redEyeIcon).to.have.lengthOf(1);
            });
            describe(', if showEditAction is true', () => {
                before(() => {
                    const tempForm = { ...fakeForm };
                    tempForm.instances_count = 0;
                    columns = formsTableColumns(
                        () => null,
                        {
                            ...defaultProps,
                            state: { currentOrgUnit: { id: 1 } },
                        },
                        true,
                        false,
                    );
                    const actionColumn = columns[columns.length - 1];
                    wrapper = shallow(
                        actionColumn.Cell({
                            original: tempForm,
                        }),
                    );
                });
                // describe(', editIcon', () => {
                //     it('should be rendered', () => {
                //         const editIcon = shallow(
                //             formDialogComponent.props().renderTrigger({
                //                 openDialog: () => null,
                //             }),
                //         );
                //         expect(editIcon).to.have.lengthOf(1);
                //     });
                //     it('should toggle openDialog on click', () => {
                //         const openDialogSpy = sinon.spy();

                //         const editIcon = shallow(
                //             formDialogComponent.props().renderTrigger({
                //                 openDialog: () => openDialogSpy(),
                //             }),
                //         );
                //         editIcon.props().onClick();
                //         expect(openDialogSpy).to.have.been.calledOnce;
                //     });
                // });
                // it('FormDialogComponent onSuccess should toggle component state on click', () => {
                //     const onSuccessSpy = sinon.spy();
                //     const tempForm = { ...fakeForm };
                //     tempForm.instances_count = 0;
                //     columns = formsTableColumns(
                //         () => null,
                //         {
                //             ...defaultProps,
                //             setState: () => onSuccessSpy(),
                //             state: { currentOrgUnit: { id: 1 } },
                //         },
                //         true,
                //         false,
                //     );
                //     const actionColumn = columns[columns.length - 1];
                //     wrapper = shallow(
                //         actionColumn.Cell({
                //             original: tempForm,
                //         }),
                //     );
                //     formDialogComponent = wrapper.find(FormDialogComponent);
                //     formDialogComponent.props().onSuccess();
                //     expect(onSuccessSpy).to.have.been.calledOnce;
                // });
            });
        });
    });
});
