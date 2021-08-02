/*******************************************************************************
 *  jUnit Artifact Needed For Testing Categories
 *******************************************************************************/

package categories;

import org.junit.extensions.cpsuite.ClasspathSuite;
import org.junit.extensions.cpsuite.ClasspathSuite.ClassnameFilters;
import org.junit.extensions.cpsuite.ClasspathSuite.ClasspathProperty;
//import org.junit.extensions.cpsuite.ClasspathSuite.IncludeJars;
import org.junit.runner.RunWith;

@RunWith(ClasspathSuite.class)
@ClasspathProperty("test.junitclasspath")
@ClassnameFilters({ "!.*\\$.*" }) // to avoid any inner classes references within the junit testcases.
//@IncludeJars(true) // comment this out if using/running from eclipse //test
public class AllTests {
}
