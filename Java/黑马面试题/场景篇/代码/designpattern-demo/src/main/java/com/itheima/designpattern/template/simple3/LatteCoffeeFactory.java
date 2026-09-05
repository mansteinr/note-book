package com.itheima.designpattern.template.simple3;

/**
 * 拿铁咖啡工厂类
 */
public class LatteCoffeeFactory implements CoffeeFactory {

    /**
     * 创建拿铁咖啡
     * @return
     */
    @Override
    public Coffee createCoffee() {
        return new LatteCoffee();
    }
}
