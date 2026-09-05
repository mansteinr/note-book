package com.itheima.designpattern.template.simple3;


/**
 * 美式咖啡工厂类
 */
public class AmericanCoffeeFactory implements CoffeeFactory {

    /**
     * 创建美式咖啡
     * @return
     */
    @Override
    public Coffee createCoffee() {
        return new AmericanCoffee();
    }
}
