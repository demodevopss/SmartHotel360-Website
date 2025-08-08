// Jenkinsfile'a Generic Webhook Trigger ekleme
triggers {
    GenericTrigger(
        genericVariables: [
            [key: 'ref', value: '$.ref']
        ],
        causeString: 'Triggered on $ref',
        token: 'smarthotel360-webhook-token',
        printContributedVariables: true,
        printPostContent: true,
        silentResponse: false,
        regexpFilterText: '$ref',
        regexpFilterExpression: 'refs/heads/master'
    )
}
