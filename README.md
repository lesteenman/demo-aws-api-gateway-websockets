Websockets with API Gateway
===========================

<description>

Running
-------
<instructions to set up sam-cli>

After setting up SAM-cli, you can run the following commands to deploy this project to your account:

```
export BUCKET_NAME=<name of the bucket you made>
export STACK_NAME=<stackname>

sam package \
        --template-file template.yaml \
        --output-template-file packaged.yaml \
        --s3-bucket $(BUCKET_NAME)
        
sam deploy \
    --template-file packaged.yaml \
    --stack-name $(STACK_NAME) \
    --capabilities CAPABILITY_IAM \
```

After deploying, you can get the websocket endpoint with:

```
aws cloudformation describe-stacks \
    --stack-name $(STACK_NAME) --query 'Stacks[].Outputs'
```

Next, you can test your websocket endpoint with [wscat](https://www.npmjs.com/package/wscat):

```
wscat -c wss://<hash>.execute-api.<region>.amazonaws.com/Prod
```

Where the url starting with `wss://` is the URL you found in the 'WebSocketURI' output.
