package com.itheima.designpattern.strategy;

/**
 * 飞机策略类
 */
public class Aircraft implements TravelStrategy{
    @Override
    public void travel() {
        System.out.println("选择飞机出行...");
    }
}
