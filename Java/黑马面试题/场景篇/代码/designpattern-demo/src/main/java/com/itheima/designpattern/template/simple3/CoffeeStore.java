package com.itheima.designpattern.template.simple3;

public class CoffeeStore {

    public static void main(String[] args) {
        //可以根据不同的工厂，创建不同的产品
        CoffeeStore coffeeStore = new CoffeeStore(new LatteCoffeeFactory());
        Coffee latte = coffeeStore.orderCoffee();
        System.out.println(latte.getName());
    }

    private CoffeeFactory coffeeFactory;

    public CoffeeStore(CoffeeFactory coffeeFactory){
        this.coffeeFactory = coffeeFactory;
    }


    public Coffee orderCoffee(){
        Coffee coffee = coffeeFactory.createCoffee();
        //添加配料
        coffee.addMilk();
        coffee.addSuqar();
        return coffee;
    }
}
