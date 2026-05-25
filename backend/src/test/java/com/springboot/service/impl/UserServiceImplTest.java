package com.springboot.service.impl;

import com.springboot.mapper.UserMapper;
import com.springboot.model.entity.User;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserServiceImplTest {

    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void userRegisterShouldPersistUsernameAndReturnUserId() {
        ReflectionTestUtils.setField(userService, "baseMapper", userMapper);
        when(userMapper.selectCount(any())).thenReturn(0L);
        when(userMapper.insert(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            if (user.getUserId() == null) {
                user.setUserId(UUID.randomUUID().toString());
            }
            return 1;
        });

        String userId = userService.userRegister("testAccount", "12345678", "12345678");

        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        verify(userMapper).insert(userCaptor.capture());
        User savedUser = userCaptor.getValue();
        Assertions.assertNotNull(savedUser.getUserId());
        Assertions.assertEquals("testAccount", savedUser.getUsername());
        Assertions.assertEquals("support_agent", savedUser.getUserRole());
        Assertions.assertEquals(savedUser.getUserId(), userId);
    }
}
