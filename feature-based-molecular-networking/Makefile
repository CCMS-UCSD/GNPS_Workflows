WORKFLOW_NAME=feature-based-molecular-networking
TOOL_FOLDER_NAME=feature-based-molecular-networking

deploy-debug:
	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version release_9 \
	update-tools --workflow-name ${TOOL_FOLDER_NAME} --workflow-version release_9

deploy-production-gnps:
	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version release_9 --production-str production \
	--config ../fabric-production-gnps.yml
	#fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password update-tools --workflow-name feature-based-molecular-networking --workflow-version release_9 --production-str production

deploy-production-proteomics:
	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password \
	update-workflow-xml --workflow-name ${WORKFLOW_NAME} --workflow-version release_9 --production-str production \
	--config ../fabric-production-proteomics.yml


# test-gnps:
# 	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password update-workflow-xml --workflow-name feature-based-molecular-networking --workflow-version release_9 --production-str production --config ../fabric-production-gnps.yml

# test-proteomics:
# 	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password update-workflow-xml --workflow-name feature-based-molecular-networking --workflow-version release_9 --production-str production --config ../fabric-production-proteomics.yml
