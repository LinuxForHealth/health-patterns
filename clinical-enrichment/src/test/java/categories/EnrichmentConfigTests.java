/*******************************************************************************
 *  jUnit Artifact Needed For Testing Categories
 *******************************************************************************/
package categories;


import org.junit.experimental.categories.Categories;
import org.junit.runner.RunWith;
import org.junit.runners.Suite.SuiteClasses;

@RunWith(Categories.class)
@SuiteClasses(AllTests.class) 
@Categories.IncludeCategory(EnrichmentConfig.class)

public class EnrichmentConfigTests {

}
