package com.ibm.healthpatterns.rest;

import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.boot.context.event.ApplicationReadyEvent;

/**
 * 
 * @author Luis A. Garía
 *
 */
@Component
public class Info {

	/**
	 * 
	 */
	@EventListener(ApplicationReadyEvent.class)
	public void contextRefreshedEvent() {
		System.out.println("The following endpoints are available by default :-");
		System.out.println("  Health        : http://localhost:8080/health");
		System.out.println("  Application   : http://localhost:8080/cohort-service/config");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries/{id}/patients");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries/{id}/patientIDs");
	}

}
