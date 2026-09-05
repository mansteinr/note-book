package com.itheima.designpattern.template.simple1;

/**
 * 咖啡接口
 */
public interface Coffee {

    /**
     *  获取名字
     * @return
     */
    public String getName();

    /**
     * 加牛奶
     */
    public void addMilk();

    /**
     * 加糖
     */
    public void addSuqar();
}
