package com.itheima.designpattern.template.simple2;

public class LatteCoffee implements Coffee {
    @Override
    public String getName() {
        return "latteCoffee";
    }

    @Override
    public void addMilk() {
        System.out.println("LatteCoffee...addMilk...");
    }

    @Override
    public void addSuqar() {
        System.out.println("LatteCoffee...addSuqar...");
    }
}
