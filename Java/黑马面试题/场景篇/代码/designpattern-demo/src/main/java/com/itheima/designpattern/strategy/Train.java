package com.itheima.designpattern.strategy;

/**
 * 火车策略类
 */
public class Train implements TravelStrategy{
    @Override
    public void travel() {
        System.out.println("选择火车出行...");
    }
}
