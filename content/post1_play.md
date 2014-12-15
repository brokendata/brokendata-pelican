Title:  Setting up Scala Activator for IDEA
Date: 2014-12-13 8:21
Tags: Scala, Activator, Play
Category: Technical Debt	
Slug: blog
Author: Ryan Wheeler
Summary: Quickly setup Play project for Idea with activator 

Quick post for posterity on setting up a activator project (specifically Play!). I already have sbt installed and configured. 

Rather than use the Play standalone, I am using the Typesafe Activator stack available [Here](https://typesafe.com/community/core-tools/activator-and-sbt)

Once you have activator installed and configured in your path, getting started is cake. Create a new project director and simply run 

```bash
activator new play-scala 
```

Great we have an default play app. 

Making things work with IDEA has been hit or miss especially with sbt when you are just starting out. The best way I have found is to bypass creating a project via the IDEA wizard and use the scala-idea plugin found [here](https://github.com/mpeltonen/sbt-idea)

By adding the following to the global build.sbt in `user/home/.sbt/plugins` 

```scala 
resolvers += "Sonatype snapshots" at "https://oss.sonatype.org/content/repositories/snapshots/"

addSbtPlugin("com.github.mpeltonen" % "sbt-idea" % "1.7.0-SNAPSHOT")

scalaVersion := "2.10.4"

```
A IDEA scala project can be created via  

```bash 
sbt gen-idea 
```
 
How to make sure our Play Project and Idea work ok? After creating the project via activator, simple run 

```bash 
activator idea 
```

And we can now load the project in idea via File| Open 


