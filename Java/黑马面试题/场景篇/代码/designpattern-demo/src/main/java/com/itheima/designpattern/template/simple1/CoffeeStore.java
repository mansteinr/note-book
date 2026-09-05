package com.itheima.designpattern.template.simple1;

/**
 * 咖啡店类
 */
public class CoffeeStore {

    public static void main(String[] args) {
        Coffee coffee = orderCoffee("latte");
        System.out.println(coffee.getName());
    }
    /**
     * 根据类型选择不同的咖啡
     * @param type
     * @return
     */
    public static Coffee orderCoffee(String type){
        Coffee coffee = null;
        if("american".equals(type)){
            coffee = new AmericanCoffee();
        }else if ("latte".equals(type)){
            coffee = new LatteCoffee();
        }
        //添加配料
        coffee.addMilk();
        coffee.addSuqar();
        return coffee;
    }
}
