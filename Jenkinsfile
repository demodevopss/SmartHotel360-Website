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

        stage('Security Scan - Trivy') {
            steps {
                script {
                    try {
                        // Trivy ile Docker kullanarak scan
                        echo "🔍 Preparing Trivy security scan..."
                        sh 'docker pull aquasec/trivy:latest'
                        
                        // Reports dizinini oluştur
                        sh 'mkdir -p security-reports'
                        
                        // Trivy vulnerability scan (Docker kullanarak)
                        sh """
                        echo "🔍 Running Trivy vulnerability scan..."
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                            -v \$(pwd)/security-reports:/tmp/security-reports \\
                            aquasec/trivy:latest image \\
                            --format table --output /tmp/security-reports/trivy-vulnerabilities.txt \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        
                        echo "📊 Generating Trivy JSON report..."
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                            -v \$(pwd)/security-reports:/tmp/security-reports \\
                            aquasec/trivy:latest image \\
                            --format json --output /tmp/security-reports/trivy-report.json \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        
                        echo "🎯 Generating Trivy SARIF report (for GitHub integration)..."
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                            -v \$(pwd)/security-reports:/tmp/security-reports \\
                            aquasec/trivy:latest image \\
                            --format sarif --output /tmp/security-reports/trivy-results.sarif \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        
                        echo "⚠️ Checking for HIGH and CRITICAL vulnerabilities..."
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                            aquasec/trivy:latest image \\
                            --severity HIGH,CRITICAL --format table \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        """
                        
                        // Basit vulnerability count check (JSON'dan)
                        def trivyExitCode = sh(
                            script: """
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                                aquasec/trivy:latest image \\
                                --severity CRITICAL --exit-code 1 --quiet \\
                                ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                            """,
                            returnStatus: true
                        )
                        
                        def trivyHighExitCode = sh(
                            script: """
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                                aquasec/trivy:latest image \\
                                --severity HIGH,CRITICAL --exit-code 1 --quiet \\
                                ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                            """,
                            returnStatus: true
                        )
                        
                        echo "🔢 Security Scan Results:"
                        echo "   CRITICAL exit code: ${trivyExitCode}"
                        echo "   HIGH+CRITICAL exit code: ${trivyHighExitCode}"
                        
                        // Security policy: Fail if CRITICAL vulnerabilities found
                        if (trivyExitCode != 0) {
                            echo "❌ CRITICAL vulnerabilities found! Failing the pipeline."
                            error("Security scan failed: CRITICAL vulnerabilities detected")
                        } else if (trivyHighExitCode != 0) {
                            echo "⚠️ HIGH vulnerabilities found. Consider reviewing."
                            echo "Pipeline continues but marked as UNSTABLE."
                            currentBuild.result = 'UNSTABLE'
                        } else {
                            echo "✅ Security scan passed!"
                        }
                        
                    } catch (Exception e) {
                        echo "⚠️ Trivy scan failed: ${e.getMessage()}"
                        echo "Continuing pipeline but marking as unstable..."
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Archive security reports
                        archiveArtifacts artifacts: 'security-reports/**', allowEmptyArchive: true
                        
                        // Publish HTML report
                        if (fileExists('security-reports/trivy-report.html')) {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'security-reports',
                                reportFiles: 'trivy-report.html',
                                reportName: 'Trivy Security Report',
                                reportTitles: 'Container Security Scan Results'
                            ])
                        }
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
                            -p 8080:8080 \\
                            --network selenium-tests_selenium-network \\
                            -e ASPNETCORE_URLS="http://0.0.0.0:8080" \\
                            ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        
                        # Container'ın başlatılmasını bekle
                        echo "Waiting for container to start..."
                        sleep 10
                        
                        # Container durumunu kontrol et
                        echo "Checking container status..."
                        docker ps | grep smarthotel-test-${env.BUILD_NUMBER} || true
                        
                        # Container network bilgilerini kontrol et
                        echo "Checking container network..."
                        docker inspect smarthotel-test-${env.BUILD_NUMBER} --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' || true
                        
                        # Container'ın hazır olmasını bekle ve health check  
                        echo "Waiting for application to be ready..."
                        i=1
                        while [ \$i -le 12 ]; do
                            # Host'tan container'a health check
                            if curl -f http://localhost:8080/ >/dev/null 2>&1; then
                                echo "✓ Application is ready after \$((i * 5)) seconds"
                                break
                            fi
                            echo "⏳ Waiting for app readiness... \$((i * 5))s (attempt \$i/12)"
                            sleep 5
                            i=\$((i + 1))
                        done
                        
                        # Final network connectivity test
                        echo "Testing container network connectivity..."
                        if ! curl -I http://localhost:8080/; then
                            echo "⚠ Health check failed! Checking container logs..."
                            echo "=== Container Logs (last 50 lines) ==="
                            docker logs --tail 50 smarthotel-test-${env.BUILD_NUMBER} || true
                            echo "=== Container Process List ==="
                            docker exec smarthotel-test-${env.BUILD_NUMBER} ps aux || true
                            echo "=== Container Port Check ==="
                            docker exec smarthotel-test-${env.BUILD_NUMBER} netstat -tuln || true
                            echo "⚠ Continuing with tests despite health check failure..."
                        else
                            echo "✅ Health check passed!"
                        fi
                        
                        # Test inter-container connectivity on same network
                        echo "🔍 Testing container-to-container network connectivity..."
                        docker run --rm --network selenium-tests_selenium-network \\
                            alpine/curl:latest curl -I http://smarthotel-test-${env.BUILD_NUMBER}:8080/ || \\
                            echo "⚠ Container-to-container connectivity failed"
                        """
                        
                        // Test URL'i container IP'si
                        def testUrl = "http://smarthotel-test-${env.BUILD_NUMBER}:8080"
                        
                        // Selenium testlerini çalıştır
                        sh """
                        cd selenium-tests
                        python3 -m venv test-venv
                        . test-venv/bin/activate
                        pip install -r requirements.txt
                        
                        # Test çalıştır - timeout artırıldı ve debug eklendi
                        python run_tests.py \\
                            --app-url ${testUrl} \\
                            --selenium-hub http://localhost:4444/wd/hub \\
                            --browser chrome \\
                            --headless \\
                            --app-timeout 120 \\
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
        env:
        - name: ASPNETCORE_URLS
          value: "http://0.0.0.0:8080"
        ports:
        - containerPort: 8080
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
      targetPort: 8080
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
                rm -rf security-reports/*.json || true
                rm -rf security-reports/*.sarif || true
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
