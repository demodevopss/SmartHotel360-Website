pipeline {
    agent {
        label 'k3s-master' // Jenkins agent'ının k3s-master VM'inde çalışmasını sağlar
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
                        // Ayrica 'latest' etiketiyle pushla
                        sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                        sh "docker push ${DOCKER_IMAGE_NAME}:latest"
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
        image: ${DOCKER_IMAGE_NAME}:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 80
"""
                        // Kubernetes Service YAML içeriği (NodePort olarak ayarlandı)
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
      nodePort: 30080
  type: NodePort
"""
                        // Geçici YAML dosyaları oluştur ve uygula
                        writeFile file: 'deployment.yaml', text: deploymentYaml
                        writeFile file: 'service.yaml', text: serviceYaml

                        sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl apply -f deployment.yaml -n ${KUBERNETES_NAMESPACE}"
                        sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl apply -f service.yaml -n ${KUBERNETES_NAMESPACE}"

                        // Rollout sağlık kontrolü ve hata durumunda log toplama
                        try {
                            sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl rollout status deploy/smarthotel-website -n ${KUBERNETES_NAMESPACE} --timeout=180s | cat"
                            sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl get deploy,po,svc -n ${KUBERNETES_NAMESPACE} -o wide | cat"
                            // NodePort erişim bilgisi
                            sh "KUBECONFIG=${KUBECONFIG_FILE} kubectl get nodes -o wide -n ${KUBERNETES_NAMESPACE} | cat"
                            echo "Uygulama NodePort ile erişilebilir: http://<NODE_IP>:30080"
                        } catch (err) {
                            echo "Rollout başarısız oldu. Pod günlükleri toplanıyor..."
                            sh '''
                            set -e
                            KUBECONFIG=${KUBECONFIG_FILE} kubectl get pods -n ${KUBERNETES_NAMESPACE}
                            for p in $(KUBECONFIG=${KUBECONFIG_FILE} kubectl get pods -n ${KUBERNETES_NAMESPACE} -o name | grep smarthotel-website || true); do
                              echo "===== $p describe =====";
                              KUBECONFIG=${KUBECONFIG_FILE} kubectl describe $p -n ${KUBERNETES_NAMESPACE} | sed -n '1,200p';
                              echo "===== $p last logs =====";
                              KUBECONFIG=${KUBECONFIG_FILE} kubectl logs $p -n ${KUBERNETES_NAMESPACE} --tail=200 || true;
                            done
                            '''
                            error "Deploy rollout başarısız"
                        }
                    }
                }
            }
        }

        stage('Selenium Tests') {
            steps {
                script {
                    // Selenium testlerini çalıştır
                    try {
                        // Selenium Grid'i başlat
                        sh '''
                        cd selenium-tests
                        docker-compose -f docker-compose.selenium.yml up -d
                        echo "Selenium Grid starting, waiting 30 seconds..."
                        sleep 30
                        '''
                        
                        // Test environment bilgilerini al
                        def nodeIP = sh(
                            script: "KUBECONFIG=${KUBECONFIG_FILE} kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type==\"InternalIP\")].address}' -n ${KUBERNETES_NAMESPACE}",
                            returnStdout: true
                        ).trim()
                        
                        def appUrl = "http://${nodeIP}:30080"
                        
                        // Selenium testlerini çalıştır
                        sh """
                        cd selenium-tests
                        python3 -m venv test-venv
                        source test-venv/bin/activate
                        pip install -r requirements.txt
                        
                        # Test çalıştır
                        python run_tests.py \\
                            --app-url ${appUrl} \\
                            --selenium-hub http://localhost:4444/wd/hub \\
                            --browser chrome \\
                            --headless \\
                            --pytest-args "--html=reports/selenium-report.html --self-contained-html --junitxml=reports/selenium-junit.xml -v"
                        """
                        
                        echo "✓ Selenium tests completed successfully"
                        
                    } catch (Exception e) {
                        echo "⚠ Selenium tests failed: ${e.getMessage()}"
                        // Test başarısız olsa da pipeline devam etsin (isteğe bağlı)
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Selenium Grid'i durdur
                        sh '''
                        cd selenium-tests
                        docker-compose -f docker-compose.selenium.yml down || true
                        '''
                        
                        // Test raporlarını arşivle
                        script {
                            if (fileExists('selenium-tests/reports/selenium-report.html')) {
                                publishHTML([
                                    allowMissing: false,
                                    alwaysLinkToLastBuild: true,
                                    keepAll: true,
                                    reportDir: 'selenium-tests/reports',
                                    reportFiles: 'selenium-report.html',
                                    reportName: 'Selenium Test Report',
                                    reportTitles: 'SmartHotel360 E2E Tests'
                                ])
                            }
                            
                            if (fileExists('selenium-tests/reports/selenium-junit.xml')) {
                                junit 'selenium-tests/reports/selenium-junit.xml'
                            }
                        }
                        
                        // Test artifact'lerini arşivle
                        archiveArtifacts artifacts: 'selenium-tests/reports/**', allowEmptyArchive: true
                    }
                }
            }
        }
    }
}
