pipeline {
    agent {
        label 'k3s-master' // Jenkins agent'ının k3s-master VM'inde çalışmasını sağlar
    }

    triggers {
        // GitHub push tetiklemesi
        githubPush()
        // SCM polling - her 2 dakikada bir kontrol
        pollSCM('H/2 * * * *')
    }

    environment {
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials' // Jenkins'e eklediğiniz Docker Registry kimlik bilgilerinin ID'si
        KUBECONFIG_CREDENTIALS_ID = 'k3s-kubeconfig' // Jenkins'e eklediğiniz kubeconfig dosyasının ID'si
        DOCKER_IMAGE_NAME = 'devopsserdar/smarthotel360-website' // Kendi Docker Registry kullanıcı adınızı kullanın
        KUBERNETES_NAMESPACE = 'default' // Uygulamanın dağıtılacağı Kubernetes namespace'i
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                git branch: 'master', credentialsId: 'github-credentials', url: 'https://github.com/demodevopss/SmartHotel360-Website.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Dockerfile'ın bulunduğu dizine git
                    dir('Source/SmartHotel360.Website') {
                        // Docker imajını oluştur
                        sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin"
                        sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                        sh "docker logout"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([file(credentialsId: env.KUBECONFIG_CREDENTIALS_ID, variable: 'KUBECONFIG_FILE')]) {
                        // Kubernetes Deployment YAML içeriği
                        def deploymentYaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smarthotel-website
  namespace: ${KUBERNETES_NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smarthotel-website
  template:
    metadata:
      labels:
        app: smarthotel-website
    spec:
      containers:
      - name: smarthotel-website
        image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
        ports:
        - containerPort: 80
"""
                        // Kubernetes Service YAML içeriği
                        def serviceYaml = """
apiVersion: v1
kind: Service
metadata:
  name: smarthotel-website-service
  namespace: ${KUBERNETES_NAMESPACE}
spec:
  selector:
    app: smarthotel-website
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer # K3s'te LoadBalancer tipi genellikle MetalLB veya benzeri bir eklenti gerektirir.
                    # Eğer yoksa NodePort kullanabilirsiniz.
"""
                        // Geçici YAML dosyaları oluştur ve uygula
                        writeFile file: 'deployment.yaml', text: deploymentYaml
                        writeFile file: 'service.yaml', text: serviceYaml

                        sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl apply -f deployment.yaml -n ${KUBERNETES_NAMESPACE}"
                        sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl apply -f service.yaml -n ${KUBERNETES_NAMESPACE}"
                    }
                }
            }
        }
    }
}
