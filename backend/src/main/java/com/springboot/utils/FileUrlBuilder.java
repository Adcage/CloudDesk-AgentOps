package com.springboot.utils;

public final class FileUrlBuilder {

    private FileUrlBuilder() {
    }

    public static String build(String basePath, String relativePath) {
        String normalizedBasePath = trimEndSlash(basePath);
        String normalizedRelativePath = trimStartSlash(relativePath);
        return normalizedBasePath + "/" + normalizedRelativePath;
    }

    private static String trimStartSlash(String path) {
        if (path == null || path.isEmpty()) {
            return "";
        }
        int start = 0;
        while (start < path.length() && path.charAt(start) == '/') {
            start++;
        }
        return path.substring(start);
    }

    private static String trimEndSlash(String path) {
        if (path == null || path.isEmpty()) {
            return "";
        }
        int end = path.length();
        while (end > 0 && path.charAt(end - 1) == '/') {
            end--;
        }
        return path.substring(0, end);
    }
}
