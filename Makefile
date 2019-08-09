BUCKET_NAME=websockets-gateway-demo-code
STACK_NAME=websockets-gateway-demo-stack

local:
	sam local start-lambda

package:
	sam package \
        --template-file template.yaml \
        --output-template-file packaged.yaml \
        --s3-bucket $(BUCKET_NAME)

deploy: package
	sam deploy \
		--template-file packaged.yaml \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_IAM \

	aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) --query 'Stacks[].Outputs'

teardown:
	aws cloudformation delete-stack --stack-name $(STACK_NAME)

redeploy: teardown deploy
