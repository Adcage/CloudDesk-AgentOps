package com.springboot.service;

import com.springboot.exception.BusinessException;
import jakarta.annotation.Resource;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
public class UserServiceTest {

    @Resource
    private UserService userService;

    @Test
    void userRegister() {
        String userAccount = "user";
        String userPassword = "";
        String checkPassword = "123456";
        Assertions.assertThrows(BusinessException.class, () -> {
            userService.userRegister(userAccount, userPassword, checkPassword);
        });
    }
}
