package com.itheima.designpattern.template.simple1;

/**
 * 拿铁咖啡
 */
public class LatteCoffee implements Coffee {
    /**
     *  获取名字
     * @return
     */
    @Override
    public String getName() {
        return "latteCoffee";
    }

    /**
     * 加牛奶
     */
    @Override
    public void addMilk() {
        System.out.println("LatteCoffee...addMilk...");
    }

    /**
     * 加糖
     */
    @Override
    public void addSuqar() {
        System.out.println("LatteCoffee...addSuqar...");
    }
}
