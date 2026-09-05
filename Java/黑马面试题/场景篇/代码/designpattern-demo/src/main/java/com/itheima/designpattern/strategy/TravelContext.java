package com.itheima.designpattern.strategy;

/**
 * 策略环境类
 * 用户连接上下文
 */
public class TravelContext {

    private TravelStrategy travelStrategy;

    public TravelContext(TravelStrategy travelStrategy){
        this.travelStrategy = travelStrategy;
    }

    public void selectTravel(){
        this.travelStrategy.travel();
    }


    public static void main(String[] args) {

        TravelContext travelContext = new TravelContext(new Car());

        travelContext.selectTravel();
    }
}
