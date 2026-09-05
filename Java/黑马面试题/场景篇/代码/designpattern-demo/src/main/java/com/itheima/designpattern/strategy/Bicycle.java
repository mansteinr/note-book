package com.itheima.designpattern.strategy;

/**
 * 自行车策略类
 */
public class Bicycle implements TravelStrategy{

    @Override
    public void travel() {
        System.out.println("选择自行车出行...");
    }
}
