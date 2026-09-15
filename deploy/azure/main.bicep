targetScope = 'resourceGroup'

@description('Existing, authorised Container Apps environment resource ID. Must support Consumption.')
param environmentId string

@description('Same Azure location as the existing environment.')
param location string

@description('Publicly pullable demo image, pinned to an immutable digest after the container smoke check.')
param containerImage string

@minLength(2)
@maxLength(32)
param appName string = 'interstellar-demo'

resource demo 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: location
  properties: {
    environmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'demo'
          image: containerImage
          env: [
            {
              name: 'DEMO_MODE'
              value: 'true'
            }
            {
              name: 'STATIC_DIR'
              value: '/app/static'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Startup'
              httpGet: {
                path: '/health'
                port: 8000
              }
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 10
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output url string = 'https://${demo.properties.configuration.ingress.fqdn}'
