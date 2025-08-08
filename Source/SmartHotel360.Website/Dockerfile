FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
ENV BuildingDocker true
WORKDIR /src
COPY SmartHotel360.Website.csproj .
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /webapp


FROM arm64v8/node:14-alpine as node
RUN apk add --no-cache python3 make g++ py3-pip
WORKDIR /src
COPY . .
WORKDIR /src/ClientApp
# CRA 1.x ve eski webpack ile uyumluluk için Node 14 kullanıldı
RUN npm install --legacy-peer-deps
RUN npm run build
RUN cp -r build/* /src/wwwroot

FROM build AS publish
WORKDIR /src/ClientApp
WORKDIR /src
RUN dotnet publish -c Release -o /webapp

FROM base AS final
WORKDIR /app
COPY --from=publish /webapp .
COPY --from=node /src/wwwroot ./wwwroot
ENTRYPOINT ["dotnet", "SmartHotel360.Website.dll"]
