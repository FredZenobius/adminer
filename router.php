<?php
// 정적 파일(CSS, JS, 이미지 등)은 PHP 내장 서버가 직접 서빙하도록 false 반환
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if (preg_match('/\.(css|js|png|gif|ico|svg|woff|woff2|ttf|eot)$/i', $uri)) {
    $file = __DIR__ . $uri;
    if (file_exists($file)) {
        return false;
    }
}
// 그 외 요청은 adminer.php로 전달
include __DIR__ . '/adminer.php';
