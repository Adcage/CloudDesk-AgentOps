package com.springboot.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.IService;
import com.springboot.model.dto.user.UserQueryRequest;
import com.springboot.model.entity.User;
import com.springboot.model.vo.LoginUserVO;
import com.springboot.model.vo.UserVO;
import java.util.List;
import jakarta.servlet.http.HttpServletRequest;

public interface UserService extends IService<User> {

    String userRegister(String username, String userPassword, String checkPassword);

    LoginUserVO userLogin(String username, String userPassword, HttpServletRequest request);

    User getLoginUser(HttpServletRequest request);

    User getLoginUserPermitNull(HttpServletRequest request);

    boolean isAdmin(HttpServletRequest request);

    boolean isAdmin(User user);

    boolean userLogout(HttpServletRequest request);

    LoginUserVO getLoginUserVO(User user);

    UserVO getUserVO(User user);

    List<UserVO> getUserVO(List<User> userList);

    QueryWrapper<User> getQueryWrapper(UserQueryRequest userQueryRequest);
}