deploy-debug:
	#fab -f ../fabfile2.py update_workflow_xml:feature-based-molecular-networking,release_9 update_tools:feature-based-molecular-networking,release_9
	fab -H proteomics2.ucsd.edu --prompt-for-login-password update-workflow-xml --workflow-name feature-based-molecular-networking --workflow-version release_9


deploy-production:
	fab -f ../fabfile2.py update_workflow_xml:feature-based-molecular-networking,release_9,production update_tools:feature-based-molecular-networking,release_9,production