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

        stage('Selenium Tests') {
            steps {
                script {
                    // Deploy edilmeden önce testleri çalıştır
                    try {
                        // Selenium Grid'i başlat
                        sh '''
                        cd selenium-tests
                        docker-compose -f docker-compose.selenium.yml up -d
                        echo "Selenium Grid starting, waiting 30 seconds..."
                        sleep 30
                        '''
                        
                        // Test için Docker container'ı geçici olarak çalıştır
                        sh """
                        echo "Starting test container..."
                        docker run -d --name smarthotel-test-${env.BUILD_NUMBER} \\
                            -p 8080:80 \\
                            --network selenium-tests_selenium-network \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        
                        # Container'ın hazır olmasını bekle
                        sleep 15
                        """
                        
                        // Test URL'i container IP'si
                        def testUrl = "http://smarthotel-test-${env.BUILD_NUMBER}:80"
                        
                        // Selenium testlerini çalıştır
                        sh """
                        cd selenium-tests
                        python3 -m venv test-venv
                        source test-venv/bin/activate
                        pip install -r requirements.txt
                        
                        # Test çalıştır
                        python run_tests.py \\
                            --app-url ${testUrl} \\
                            --selenium-hub http://localhost:4444/wd/hub \\
                            --browser chrome \\
                            --headless \\
                            --pytest-args "--html=reports/selenium-report.html --self-contained-html --junitxml=reports/selenium-junit.xml -v"
                        """
                        
                        echo "✓ Selenium tests passed - proceeding with deployment"
                        
                    } catch (Exception e) {
                        echo "✗ Selenium tests failed: ${e.getMessage()}"
                        echo "Deployment will be skipped due to test failures"
                        currentBuild.result = 'FAILURE'
                        error "Selenium tests failed - stopping pipeline"
                    } finally {
                        // Test container'ı temizle
                        sh """
                        docker stop smarthotel-test-${env.BUILD_NUMBER} || true
                        docker rm smarthotel-test-${env.BUILD_NUMBER} || true
                        """
                        
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
    }
    
    post {
        always {
            script {
                echo "🧹 Pipeline cleanup başlıyor..."
                
                // Docker temizligi
                sh '''
                echo "Kullanılmayan Docker image'larını temizliyorum..."
                docker image prune -f || true
                docker container prune -f || true
                docker volume prune -f || true
                docker network prune -f || true
                
                echo "Dangling image'ları temizliyorum..."
                docker rmi $(docker images -f "dangling=true" -q) || true
                
                echo "7 günden eski image'ları temizliyorum..."
                docker image prune -a --filter "until=168h" -f || true
                '''
                
                // Workspace temizligi
                sh '''
                echo "Workspace cache temizliyorum..."
                find . -name "node_modules" -type d -exec rm -rf {} + || true
                find . -name "*.log" -type f -delete || true
                find . -name "*.tmp" -type f -delete || true
                '''
                
                // Test artifacts temizligi
                sh '''
                echo "Test dosyalarını temizliyorum..."
                rm -rf selenium-tests/test-venv || true
                rm -rf selenium-tests/reports/*.png || true
                find . -name "__pycache__" -type d -exec rm -rf {} + || true
                '''
                
                // Disk durumu raporu
                sh '''
                echo "📊 Temizlik sonrası disk durumu:"
                df -h / || true
                echo "🐳 Docker disk kullanımı:"
                docker system df || true
                '''
                
                echo "✅ Pipeline cleanup tamamlandı!"
            }
        }
        success {
            echo "🎉 Pipeline başarılı - Uygulama deploy edildi!"
        }
        failure {
            echo "❌ Pipeline başarısız - Deployment yapılmadı!"
        }
        unstable {
            echo "⚠️ Pipeline kararsız - Testlerde problem var!"
        }
    }
}
