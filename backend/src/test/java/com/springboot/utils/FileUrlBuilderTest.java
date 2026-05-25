package com.springboot.utils;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class FileUrlBuilderTest {

    @Test
    void shouldJoinBasePathAndRelativePathWithoutDoubleSlash() {
        String result = FileUrlBuilder.build("/api/files/", "/user_avatar/a.png");
        Assertions.assertEquals("/api/files/user_avatar/a.png", result);
    }
}
