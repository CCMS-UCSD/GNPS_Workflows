WORKFLOW_NAME=feature-based-molecular-networking
TOOL_FOLDER_NAME=feature-based-molecular-networking
WORKFLOW_VERSION=release_9
USERNAME=miw023

deploy-debug:
	fab2 -H ${USERNAME}@proteomics2.ucsd.edu --prompt-for-login-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version ${WORKFLOW_VERSION} \
	update-tools --workflow-name ${TOOL_FOLDER_NAME} --workflow-version ${WORKFLOW_VERSION}

deploy-production-gnps:
	fab2 -H ${USERNAME}@gnps.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version ${WORKFLOW_VERSION} \
	update-tools --workflow-name ${TOOL_FOLDER_NAME} --workflow-version ${WORKFLOW_VERSION} \
	--production-str production \
	--config ../fabric-production-gnps.yml

deploy-production-proteomics:
	fab2 -H ${USERNAME}@proteomics.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version release_9 \
	update-tools --workflow-name ${TOOL_FOLDER_NAME} --workflow-version ${WORKFLOW_VERSION} \
	--production-str production \
	--config ../fabric-production-proteomics.yml

