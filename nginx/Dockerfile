FROM nginx:alpine

# 复制配置
COPY conf.d /etc/nginx/conf.d/

# SSL 证书目录
RUN mkdir -p /etc/nginx/ssl

# 注释掉默认的 nginx.conf 中的 server 块冲突
RUN sed -i '/include \/etc\/nginx\/conf.d\/\*.conf;/!d' /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
