deploy-debug:
	#fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password update-workflow-xml --workflow-name feature-based-molecular-networking --workflow-version release_9
	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password update-tools --workflow-name feature-based-molecular-networking --workflow-version release_9

deploy-production:
	fab2 -H miw023@proteomics2.ucsd.edu --prompt-for-login-password --prompt-for-sudo-password update-tools --workflow-name feature-based-molecular-networking --workflow-version release_9 --production-str production