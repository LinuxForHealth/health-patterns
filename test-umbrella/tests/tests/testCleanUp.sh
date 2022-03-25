#!/bin/bash

# Looking for test failures. If any are found, then save the environment for debug 
TEST_FAILURE=$(cat target/surefire-reports/*.txt | grep FAILURE!)
echo $TEST_FAILURE
if [[ $TEST_FAILURE == *"FAILURE!"* ]]
then
   echo "********************************************************************"
   echo "*  Test Failures detected.  Saving the test environment for debug. *"
   echo "********************************************************************"
   export ENV_CLEAN_UP="false"
else
   echo "*********************************"
   echo "*  No Test Failures detected.   *"
   echo "*********************************"  
fi

# ENV_CLEAN_UP is set in the toolchain environment properties.  The default value is true, but it can be changed on toolchain start
# It can can be set to false if test errors are detected
# if we need to keep the test environment available for debug
if [ $ENV_CLEAN_UP = "true" ]  
then
	# then clean up
	echo "*************************************"
	echo "* Delete the Deployment             *"
	echo "*************************************"
	helm3 delete $HELM_RELEASE
	if [ $DEPLOY_NIFIKOP = "true" ]
	then
		echo "*************************************"
		echo "* Waiting for 30  seconds           *"
		echo "*************************************"
		date
		sleep 30   
		date
		echo "*************************************"
		echo "* Delete NifiKop                    *"
		echo "*************************************"
		helm3 delete nifikop
	fi	
	echo "*************************************"
	echo "* Waiting for 30  seconds           *"
	echo "*************************************"
	date
	sleep 30  
	date
	echo "*************************************"
	echo "* Delete PVCs                       *"
	echo "*************************************"
	kubectl delete pvc -l release=$HELM_RELEASE
        kubectl delete pv -l release=$HELM_RELEASE
	echo "*************************************"
	echo "* Waiting for 30  seconds           *"
	echo "*************************************"
	date
	sleep 30  
	date
	echo "*************************************"
	echo "* Delete Namespace                  *"
	echo "*************************************"
	kubectl delete namespace $TEST_NAMESPACE	
else
    # save the test deployment
	echo "*************************************************************"
	echo "* Test deployment "$HELM_RELEASE" in "$TEST_NAMESPACE" saved            *"
	echo "*************************************************************"
fi
