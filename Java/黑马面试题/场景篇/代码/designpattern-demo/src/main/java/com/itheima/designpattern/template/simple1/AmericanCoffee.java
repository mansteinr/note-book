package com.itheima.designpattern.template.simple1;

/**
 * 美式咖啡
 */
public class AmericanCoffee implements Coffee {

    /**
     *  获取名字
     * @return
     */
    @Override
    public String getName() {
        return "americanCoffee";
    }

    /**
     * 加牛奶
     */
    @Override
    public void addMilk() {
        System.out.println("AmericanCoffee...addMilk...");
    }

    /**
     * 加糖
     */
    @Override
    public void addSuqar() {
        System.out.println("AmericanCoffee...addSuqar...");
    }
}
