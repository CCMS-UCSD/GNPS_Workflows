# GNPS ProteoSAFe Workflows

This public repository contains the GNPS Workflows running on GNPS [(http://gnps.ucsd.edu)](http://gnps.ucsd.edu).

## Contribute to GNPS

The GNPS community is always welcoming suggestions and contributions. Be part of the community and contribute !

### GitHub Repositories
Your are kindly invited to open "issues" on our GitHub repositories, and propose changes to our Documentation and Workflows. We are also welcoming direct pull request on the respective repository.

**GNPS_Documentation** GitHub respository that points to the documentation website [(https://ccms-ucsd.github.io/GNPSDocumentation)](https://ccms-ucsd.github.io/GNPSDocumentation).

- [https://github.com/CCMS-UCSD/GNPSDocumentation](https://github.com/CCMS-UCSD/GNPSDocumentation)

**GNPS_Workflows** Present GitHub repository that contains the workflows available on GNPS [(http://gnps.ucsd.edu)](http://gnps.ucsd.edu):

- [http://github.com/CCMS-UCSD/GNPS_Workflows](http://github.com/CCMS-UCSD/GNPS_Workflows)


### GNPS Forum
Discussions and suggestions can also take place on the GNPS forum at [https://groups.google.com/forum/#!forum/molecular_networking_bug_reports](https://groups.google.com/forum/#!forum/molecular_networking_bug_reports).


## GNPS Core Webserver Status

GNPS Integration Web and Workflow jobs are handled in the [CCMS-Integration-Tests Repository](https://github.com/CCMS-UCSD/CCMS-Integration-Tests).

| Feature  | Server Status |
|---|---|
| GNPS/Beta/MassIVE API Tests | ![web-ccms-api](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/web-ccms-api/badge.svg) |
| GNPS/Beta/MassIVE Selenium Tests | ![web-ccms-selenium](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/web-ccms-selenium/badge.svg) |
| GNPS Workflows Fast Test | ![workflow-proteomics3-fast](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/workflow-gnps-fast/badge.svg) |
| Beta Workflows Fast Test | ![workflow-proteomics3-fast](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/workflow-proteomics3-fast/badge.svg) |
| GNPS Full Workflows Test | ![workflow-gnps](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/workflow-gnps/badge.svg) |
| Beta Full Workflows Test | ![workflow-beta](https://github.com/CCMS-UCSD/CCMS-Integration-Tests/workflows/workflow-beta/badge.svg) |

Uptime Robot Monitor - [https://stats.uptimerobot.com/Am4PLUWn3](https://stats.uptimerobot.com/Am4PLUWn3)

## Specific Workflow Tests

| Workflow  | GNPS Link  | Beta Link  | Unit Test | 
|---|---|---|---|
| Molecular Networking  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22METABOLOMICS-SNETS-V2%22,%22library_on_server%22:%22d.speclibs;%22%7D)  | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22METABOLOMICS-SNETS-V2%22,%22library_on_server%22:%22d.speclibs;%22%7D) | ![](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-networking/badge.svg) | 
| Large Scale Library Search  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLECULAR-LIBRARYSEARCH-V2%22,%22library_on_server%22:%22d.speclibs;%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLECULAR-LIBRARYSEARCH-V2%22,%22library_on_server%22:%22d.speclibs;%22%7D) |---|
| MASST  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22SEARCH_SINGLE_SPECTRUM%22,%22library_on_server%22:%22d.speclibs;%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22SEARCH_SINGLE_SPECTRUM%22,%22library_on_server%22:%22d.speclibs;%22%7D) |---|
| Feature-Based Molecular Networking  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22FEATURE-BASED-MOLECULAR-NETWORKING%22,%22library_on_server%22:%22d.speclibs;%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22FEATURE-BASED-MOLECULAR-NETWORKING%22,%22library_on_server%22:%22d.speclibs;%22%7D) |![](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-fbmn/badge.svg)| 
| MS2LDA Motif DB  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MS2LDA_MOTIFDB%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MS2LDA_MOTIFDB%22%7D) | ![workflow-unit-ms2lda](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-ms2lda/badge.svg) |
| MolNetEnhancer/MetaboDistTree  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLNETENHANCER%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLNETENHANCER%22%7D) |![](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-molnet/badge.svg)|
| MSMS-Chooser  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MSMS-CHOOSER%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MSMS-CHOOSER%22%7D) |---|
| OpenMS Feature Detector for FBMN - Future Feature  | [Workflow]()   | [Workflow]() |---|
| MSHub-GC Deconvolution  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B"workflow":"MSHUB-GC"%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B"workflow":"MSHUB-GC"%7D) |![](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-gc-mshub/badge.svg)|
| Library Search/Molecular Networking GC  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLECULAR-LIBRARYSEARCH-GC%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLECULAR-LIBRARYSEARCH-GC%22%7D) |![](https://github.com/CCMS-UCSD/GNPS_Workflows/workflows/workflow-unit-gc-networking/badge.svg)|
| Merge Polarity Networks  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MERGE_NETWORKS_POLARITY%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MERGE_NETWORKS_POLARITY%22%7D) | ![](https://github.com/mwang87/MergePolarity/workflows/unit-test/badge.svg) |
| Microbiome-Metabolomics Association - mmvec  | [Workflow - Inactive](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MMVEC%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MMVEC%22%7D) |---|
| Sirius - Bocker Lab | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22SIRIUS%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22SIRIUS%22%7D) |---|
| Qemistree | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22QEMISTREE%22%7D)   | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22QEMISTREE%22%7D) |---|
| LC - MZMine2 | [Beta Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22LC_MZMINE2%22%7D) | [Workflow](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22LC_MZMINE2%22%7D) |---|
| Legacy Networking  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22METABOLOMICS-SNETS%22,%22library_on_server%22:%22d.speclibs;%22%7D)  | --- | --- | 
| Legacy Library Search  | [Workflow](https://gnps.ucsd.edu/ProteoSAFe/index.jsp?params=%7B%22workflow%22:%22MOLECULAR-LIBRARYSEARCH%22,%22library_on_server%22:%22d.speclibs;%22%7D)   | --- |---| 



## GNPS Documentation

Build: ![](https://github.com/CCMS-UCSD/GNPSDocumentation/workflows/CI/badge.svg)

## GNPS Microservices Links/Status

| Link  | Description  | Status |
|---|---|---|
| gnps-external.ucsd.edu | Linking out structures to external services (e.g. NPAtlas) | ![](https://github.com/mwang87/GNPS_ExternalStructureProxy/workflows/production-integration/badge.svg) |
| gnps-classyfire.ucsd.edu | Classyfire caching proxy for GNPS | ![](https://github.com/mwang87/ClassyfireProxy/workflows/production-integration/badge.svg) |
| gnps-structure.ucsd.edu | Structure processing worker | ![](https://github.com/mwang87/ChemicalStructureWebService/workflows/production-integration/badge.svg) |
| [redu.ucsd.edu](https://redu.ucsd.edu/) | Reuse of Public Data/Sample Information | ![](https://github.com/mwang87/ReDU-MS2-GNPS/workflows/production-integration/badge.svg) |
| [gnps-quickstart.ucsd.edu](https://gnps-quickstart.ucsd.edu/) | GNPS Quickstart Server | ![](https://github.com/mwang87/GNPS_quickstart/workflows/production-integration/badge.svg) |
| [gnps-cytoscape.ucsd.edu](https://gnps-cytoscape.ucsd.edu/) | GNPS Cytoscape Export/Styling Server | ![](https://github.com/mwang87/GNPS_CytoscapeFormatting/workflows/production-integration/badge.svg) |
| [masst.ucsd.edu](https://masst.ucsd.edu/) | GNPS MASST Query Server | ![](https://github.com/mwang87/GNPS_MASST/workflows/production-integration/badge.svg) |
| [metabolomics-usi.ucsd.edu](https://metabolomics-usi.ucsd.edu/) | Metabolomics USI Server | ![](https://github.com/mwang87/MetabolomicsSpectrumResolver/workflows/production-integration/badge.svg) |
| [qemistree.ucsd.edu](https://qemistree.ucsd.edu/) | Qemistree Dashboard Server | --- |


## Testing

### Unit Testing

We have a limited number of unit tests for GNPS workflows. A test folder can be found in each workflow folder. 

To run all unit tests on a consistent platform as github actions, we use [act](https://github.com/nektos/act).

```make test-push-full```

We also have targets for individual tests, e.g.:

```make test-fbmn```

Inside the test folder, we recommend use the testing tool nose2. Execute the following code to run the workflow specific tests

```nose2 -v```


### Integration Testing

In order to add specific examples of workflow on GNPS to make sure they are tested periodically, you can add to our test files. Specifically for each workflow we have a list of test tasks that we clone and run every 12 hours. These can be found in the test-integration-workflow folder for each workflow. 


## Workflow Deployments

In order to deploy workflows, we have included the workflow deployment packages from CCMS. Specifically, we will want to follow the guide [here](https://github.com/CCMS-UCSD/CCMSDeployments). 

Once you have checked out this repository, make sure to have all the submodules checked out as well. Then you will need to follow these [steps](https://github.com/CCMS-UCSD/CCMSDeployments#necessary-steps-to-get-working). 

Then we can get a workflow onto proteomics2. To test it without over-writing the default version, you can use this command:

```make deploy-debug```

as outlined [here](https://github.com/CCMS-UCSD/CCMSDeployments#to-deploy-a-single-test-workflow).
