package com.itheima.designpattern.strategy;

/**
 * 汽车策略类
 */
public class Car implements TravelStrategy{
    @Override
    public void travel() {
        System.out.println("选择汽车出行...");
    }
}
