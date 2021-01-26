/**
 * 
 */
package com.ibm.healthpatterns.app;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.nio.file.Paths;

import org.junit.Test;

/**
 * @author Luis A. Garía
 *
 */
public class CQLFileTest {

	/**
	 * 
	 * @throws IOException
	 */
	@Test
	public void testLoadCQLFile() throws IOException {
		CQLFile file = new CQLFile(Paths.get("src/test/resources/test.cql"));
		assertEquals("Test", file.getName());
		assertEquals("1.0.0", file.getVersion());
	}

}
